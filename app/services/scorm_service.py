import os
import zipfile
import shutil
import xml.etree.ElementTree as ET

def process_scorm_package(zip_file_or_path, scorm_id_str, upload_base_folder):
    """
    Extracts a SCORM zip file into upload_base_folder/scorm/<scorm_id_str>/
    and parses imsmanifest.xml to locate the launch file (href).
    Returns (launch_href, error_message).
    """
    scorm_folder = os.path.join(upload_base_folder, 'scorm', str(scorm_id_str))
    os.makedirs(scorm_folder, exist_ok=True)

    zip_path = os.path.join(scorm_folder, 'package.zip')
    
    if isinstance(zip_file_or_path, str):
        if zip_file_or_path != zip_path and os.path.exists(zip_file_or_path):
            shutil.copy2(zip_file_or_path, zip_path)
    elif hasattr(zip_file_or_path, 'save'):
        if hasattr(zip_file_or_path, 'seek'):
            zip_file_or_path.seek(0)
        zip_file_or_path.save(zip_path)
        if hasattr(zip_file_or_path, 'seek'):
            zip_file_or_path.seek(0)
    elif hasattr(zip_file_or_path, 'read'):
        if hasattr(zip_file_or_path, 'seek'):
            zip_file_or_path.seek(0)
        with open(zip_path, 'wb') as f:
            f.write(zip_file_or_path.read())
        if hasattr(zip_file_or_path, 'seek'):
            zip_file_or_path.seek(0)

    try:
        if not isinstance(zip_file_or_path, str):
            from app.services.b2_service import upload_file_to_b2
            upload_file_to_b2(zip_file_or_path, f"{scorm_id_str}.zip" if not str(scorm_id_str).endswith('.zip') else str(scorm_id_str), folder='scorm', content_type='application/zip')
    except Exception as b2_err:
        print(f"SCORM B2 upload notice: {b2_err}")

    if not os.path.exists(zip_path):
        return None, "SCORM package file missing."

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(scorm_folder)
    except Exception as e:
        return None, f"Failed to extract SCORM zip package: {e}"

    manifest_path = os.path.join(scorm_folder, 'imsmanifest.xml')
    if not os.path.exists(manifest_path):
        for root_dir, dirs, files in os.walk(scorm_folder):
            if 'imsmanifest.xml' in [f.lower() for f in files]:
                manifest_path = os.path.join(root_dir, 'imsmanifest.xml')
                break

    if os.path.exists(manifest_path):
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]

            resource = root.find('.//resource')
            if resource is not None and 'href' in resource.attrib:
                launch_href = resource.attrib['href']
                rel_base = os.path.relpath(os.path.dirname(manifest_path), scorm_folder)
                if rel_base and rel_base != '.':
                    launch_href = os.path.join(rel_base, launch_href)
                return launch_href.replace('\\', '/'), None
        except Exception as e:
            print(f"Error parsing SCORM imsmanifest.xml: {e}")

    for root_dir, dirs, files in os.walk(scorm_folder):
        for f in files:
            if f.lower() in ['indexapi.html', 'index.html', 'story.html', 'index_lms.html', 'launch.html']:
                rel_path = os.path.relpath(os.path.join(root_dir, f), scorm_folder)
                return rel_path.replace('\\', '/'), None

    return None, "Could not identify launch HTML file in SCORM manifest."

