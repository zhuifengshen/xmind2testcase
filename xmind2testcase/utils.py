#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import json
import logging
import zipfile
import xmind
from xml.etree import ElementTree as ET

# 设置日志
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_absolute_path(path):
    """
    Return the absolute path of a file
    """
    if not path:
        return None

    if os.path.isabs(path):
        return path
    else:
        return os.path.abspath(path)


def get_xmind_content(file_path):
    """
    Extract content from XMind file, supporting both old and new formats
    """
    file_path = get_absolute_path(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XMind file {file_path} not exist!")

    # First try to read with new format
    try:
        logger.debug("Trying to read XMind file with new format handler first")
        xmind_content = read_xmind_new_format(file_path)
        logger.debug(f"Successfully loaded XMind file with new format handler")
        return xmind_content
    except Exception as e1:
        logger.debug(f"Failed to load with new format handler: {str(e1)}")

        # Then try using xmind library (for old formats)
        try:
            workbook = xmind.load(file_path)

            # Check if it's a WorkbookDocument (new xmind library) or a list (old library)
            if hasattr(workbook, 'getPrimarySheet'):
                # It's a WorkbookDocument object from newer xmind library
                logger.debug("Detected WorkbookDocument object, converting to compatible format")
                xmind_content = []

                # Get all sheets
                for sheet in workbook.getSheets():
                    sheet_dict = {
                        'title': sheet.getTitle(),
                        'topic': convert_workbook_topic(sheet.getRootTopic())
                    }
                    xmind_content.append(sheet_dict)
            else:
                # It's already in the expected format (list)
                xmind_content = workbook

            logger.debug(f"Successfully loaded XMind file with xmind library")
            return xmind_content

        except Exception as e2:
            # Try manual parsing as a last resort
            try:
                logger.debug("Trying manual parsing as a last resort")
                xmind_content = manual_parse_xmind(file_path)
                if xmind_content:
                    logger.debug("Successfully parsed XMind file manually")
                    return xmind_content
                else:
                    logger.error("Manual parsing returned empty result")
            except Exception as e3:
                logger.error(f"All parsing methods failed: {str(e1)}, {str(e2)}, {str(e3)}")

            raise ValueError(f"Failed to parse XMind file with all available methods")


def convert_workbook_topic(topic):
    """
    Convert WorkbookTopic to the expected dictionary format
    """
    if not topic:
        return {}

    result = {
        'title': topic.getTitle() or '',
        'note': get_topic_notes(topic),
        'comment': '',  # WorkbookTopic doesn't have direct comment access
        'markers': get_topic_markers(topic),
        'label': get_topic_labels(topic)
    }

    # Handle subtopics
    children = topic.getSubTopics()
    if children:
        result['topics'] = [convert_workbook_topic(child) for child in children]

    return result


def get_topic_notes(topic):
    """Extract notes from WorkbookTopic"""
    notes = topic.getNotes()
    if notes:
        return notes.getContent() or ''
    return ''


def get_topic_markers(topic):
    """Extract markers from WorkbookTopic"""
    markers = []

    # Extract markers like priority, task-done, etc.
    for marker in topic.getMarkers() or []:
        marker_id = marker.getMarkerId()
        if marker_id:
            markers.append(marker_id)

    return markers


def get_topic_labels(topic):
    """Extract labels from WorkbookTopic"""
    labels = topic.getLabels()
    if labels and len(labels) > 0:
        return labels[0]
    return ''


def read_xmind_new_format(file_path):
    """
    Read content from new XMind file format
    New XMind file is actually a ZIP file containing JSON content
    """
    content = []

    with zipfile.ZipFile(file_path, 'r') as xmind_zip:
        # Log available files
        files = xmind_zip.namelist()
        logger.debug(f"Files in XMind: {files}")

        # Read content.json file
        if 'content.json' in files:
            try:
                with xmind_zip.open('content.json') as f:
                    json_content = f.read().decode('utf-8')
                    logger.debug(f"content.json size: {len(json_content)} bytes")
                    content_data = json.loads(json_content)

                # Convert to format compatible with old version
                for sheet in content_data:
                    sheet_dict = {
                        'title': sheet.get('title', 'Untitled'),
                        'topic': convert_new_topic_format(sheet.get('rootTopic', {}))
                    }
                    content.append(sheet_dict)
            except Exception as e:
                logger.error(f"Error parsing content.json: {str(e)}")
                # If we can't parse content.json, extract it for inspection
                with xmind_zip.open('content.json') as f:
                    with open('debug_content.json', 'wb') as debug_file:
                        debug_file.write(f.read())
                logger.debug("Saved content.json to debug_content.json for inspection")
                raise
        else:
            raise ValueError("content.json not found in XMind file")

    return content


def convert_new_topic_format(new_topic):
    """
    Convert new XMind topic format to format compatible with old version
    """
    old_format = {
        'title': new_topic.get('title', ''),
        'note': extract_note_content(new_topic.get('notes', {})),
        'comment': extract_comment_content(new_topic.get('comments', [])),
        'markers': extract_markers(new_topic.get('markers', [])),
        'label': extract_label(new_topic.get('labels', []))
    }

    # Handle subtopics
    if 'children' in new_topic and 'attached' in new_topic['children']:
        old_format['topics'] = [
            convert_new_topic_format(child)
            for child in new_topic['children']['attached']
        ]

    return old_format


def extract_note_content(notes):
    """Extract note content from new format"""
    if not notes:
        return ''

    # In new version, notes may have multiple formats, prefer plain format
    if 'plain' in notes:
        return notes['plain'].get('content', '')

    return ''


def extract_comment_content(comments):
    """Extract comment content from new format"""
    if not comments or len(comments) == 0:
        return ''

    # Combine all comment contents
    return '\n'.join([comment.get('content', '') for comment in comments])


def extract_markers(markers):
    """Extract marker information from new format"""
    if not markers:
        return []

    result = []

    # Process priority markers and other markers
    for marker in markers:
        marker_id = marker.get('markerId', '')
        if marker_id.startswith('priority'):
            result.append(marker_id)
        elif marker_id in ['task-done', 'symbol-right', 'symbol-wrong',
                           'symbol-pause', 'symbol-minus']:
            result.append(marker_id)

    return result


def extract_label(labels):
    """Extract label information from new format"""
    if not labels or len(labels) == 0:
        return ''

    # Return first label
    return labels[0] if labels else ''


def manual_parse_xmind(file_path):
    """
    Manually parse XMind file without relying on any external library
    """
    result = []

    with zipfile.ZipFile(file_path, 'r') as xmind_zip:
        # Try content.json first
        if 'content.json' in xmind_zip.namelist():
            with xmind_zip.open('content.json') as f:
                content_json = f.read().decode('utf-8')

            try:
                sheets = json.loads(content_json)
                for sheet in sheets:
                    sheet_data = {
                        'title': sheet.get('title', 'Untitled'),
                        'topic': {}
                    }

                    root_topic = sheet.get('rootTopic', {})
                    if root_topic:
                        sheet_data['topic'] = {
                            'title': root_topic.get('title', ''),
                            'topics': []
                        }

                        # Process children
                        children = root_topic.get('children', {}).get('attached', [])
                        for child in children:
                            child_data = {
                                'title': child.get('title', '')
                            }
                            sheet_data['topic']['topics'].append(child_data)

                    result.append(sheet_data)
            except Exception as e:
                logger.error(f"Error in manual parsing of content.json: {str(e)}")

        # If content.json failed or not found, try content.xml
        if not result and 'content.xml' in xmind_zip.namelist():
            with xmind_zip.open('content.xml') as f:
                content_xml = f.read().decode('utf-8')

            try:
                root = ET.fromstring(content_xml)
                for sheet in root.findall('.//sheet'):
                    sheet_data = {
                        'title': sheet.get('title', 'Untitled'),
                        'topic': {}
                    }

                    topic = sheet.find('.//topic')
                    if topic is not None:
                        sheet_data['topic'] = {
                            'title': topic.get('title', '')
                        }

                    result.append(sheet_data)
            except Exception as e:
                logger.error(f"Error in manual parsing of content.xml: {str(e)}")

    return result


def extract_and_check_content_json(file_path):
    """
    Extract content.json from XMind file and check its structure
    """
    with zipfile.ZipFile(file_path, 'r') as xmind_zip:
        if 'content.json' in xmind_zip.namelist():
            with xmind_zip.open('content.json') as f:
                content = f.read().decode('utf-8')

            # Save to a file for inspection
            with open('extracted_content.json', 'w', encoding='utf-8') as f:
                f.write(content)

            # Try to parse it
            try:
                data = json.loads(content)
                print(f"Successfully parsed content.json, found {len(data)} sheets")
                return True
            except json.JSONDecodeError as e:
                print(f"Failed to parse content.json: {str(e)}")
                return False
        else:
            print("content.json not found in the XMind file")
            return False


def get_xmind_testsuites(file_path):
    """
    Get XMind file content and convert to testsuites
    """
    from xmind2testcase.parser import xmind_to_testsuites
    xmind_content = get_xmind_content(file_path)
    return xmind_to_testsuites(xmind_content)


def get_xmind_testcase_list(file_path):
    """
    Get testcase list from XMind file
    This function is used by zentao.py
    """
    testsuite_list = get_xmind_testsuites(file_path)
    testcase_list = []

    for testsuite in testsuite_list:
        testcase_list.extend(testsuite.extract_testcases())

    return testcase_list


def get_xmind_testsuite_list(file_path):
    """
    Get testsuite list from XMind file
    """
    testsuite_list = get_xmind_testsuites(file_path)
    suite_data_dict = {}
    for testsuite in testsuite_list:
        suite_data = testsuite.to_dict()
        for suite_key in suite_data:
            if suite_key not in suite_data_dict:
                suite_data_dict[suite_key] = suite_data[suite_key]
            else:
                if isinstance(suite_data_dict[suite_key], list):
                    suite_data_dict[suite_key].extend(suite_data[suite_key])

    return [suite_data_dict]


def xmind_testsuite_to_json_file(testsuite_list, json_file):
    """
    Convert XMind testsuite to JSON file
    """
    if not json_file:
        return

    with open(json_file, 'w', encoding='utf8') as f:
        f.write(json.dumps(testsuite_list, indent=4, separators=(',', ': '), ensure_ascii=False))

    return json_file


def xmind_testsuites_to_json_file(xmind_file, json_file=None):
    """
    Convert XMind file to JSON file
    """
    testsuite_list = get_xmind_testsuite_list(xmind_file)

    if not json_file:
        json_file = xmind_file[:-6] + '.json' if xmind_file.endswith('.xmind') else xmind_file + '.json'

    return xmind_testsuite_to_json_file(testsuite_list, json_file)


def xmind_testcase_to_json_file(xmind_file):
    """
    Convert XMind file to JSON file
    """
    return xmind_testsuites_to_json_file(xmind_file)


def get_xml_element_dict(element):
    """Convert XML element to dict"""
    result = {}
    for child in list(element):
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(get_xml_element_dict(child))
        else:
            result[child.tag] = get_xml_element_dict(child)

    if list(element) == []:
        return element.text
    else:
        return result


def get_xml_root_dict(xml_content):
    """Convert XML content to dict"""
    root = ET.fromstring(xml_content)
    return {root.tag: get_xml_element_dict(root)}


def convert_xml_topic(topic_element):
    """
    Convert XML topic element to the expected dictionary format
    """
    if topic_element is None:
        return {}

    result = {
        'title': topic_element.get('title', ''),
        'note': '',
        'comment': '',
        'markers': [],
        'label': ''
    }

    # Handle notes
    notes_element = topic_element.find('.//notes')
    if notes_element is not None:
        plain_element = notes_element.find('.//plain')
        if plain_element is not None and plain_element.text:
            result['note'] = plain_element.text

    # Handle markers
    markers_element = topic_element.find('.//marker-refs')
    if markers_element is not None:
        for marker_ref in markers_element.findall('.//marker-ref'):
            marker_id = marker_ref.get('marker-id')
            if marker_id:
                result['markers'].append(marker_id)

    # Handle labels
    labels_element = topic_element.find('.//labels')
    if labels_element is not None:
        label_element = labels_element.find('.//label')
        if label_element is not None and label_element.text:
            result['label'] = label_element.text

    # Handle subtopics
    children = topic_element.findall('./children/topics/topic')
    if children:
        result['topics'] = [convert_xml_topic(child) for child in children]

    return result


def main():
    """
    Main function for testing
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python utils.py <xmind_file>")
        return

    xmind_file = sys.argv[1]

    # First, check if content.json is valid
    print(f"Checking {xmind_file}...")
    if extract_and_check_content_json(xmind_file):
        print("content.json is valid, proceeding with conversion")
    else:
        print("Warning: content.json might be invalid, will try other methods")

    # Try to convert the file
    try:
        json_file = xmind_testcase_to_json_file(xmind_file)
        print(f"Successfully converted to {json_file}")
    except Exception as e:
        print(f"Error converting file: {str(e)}")

        # Try manual parsing as a last resort
        try:
            content = manual_parse_xmind(xmind_file)
            if content:
                manual_json_file = xmind_file + '.manual.json'
                with open(manual_json_file, 'w', encoding='utf8') as f:
                    f.write(json.dumps(content, indent=4, ensure_ascii=False))
                print(f"Manually parsed and saved to {manual_json_file}")
            else:
                print("Manual parsing failed")
        except Exception as e2:
            print(f"Manual parsing error: {str(e2)}")


if __name__ == "__main__":
    main()
