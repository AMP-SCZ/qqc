from pathlib import Path
from qqc.utils.files import get_nondmri_data
from qqc.utils.visualize import create_image_signal_figure
from qqc.qqc.figures import quick_figures

def test_quick_figures():
    subject_dir = Path('/data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-GW/ses-202311151')
    outdir = Path('.')

    fmri_dir = subject_dir / 'func'
    dataset = []
    for nifti_path in fmri_dir.glob('*.nii.gz'):
        if 'sbref' not in nifti_path.name:
            nifti_prefix = nifti_path.parent / nifti_path.name.split('.')[0]
            data = get_nondmri_data(nifti_prefix, 'nifti_prefix', '', False)
            dataset.append((data, nifti_prefix.name.split('ses-')[1]))

    create_image_signal_figure(
            dataset, outdir / '09_summary_fmri.png',
            True, 4, wide_fig=True)


def test_get_gifs_for_all():
    rawdata_root = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata')
    qqc_root = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/')
    sl_sessions = rawdata_root.glob('sub-*/ses-*')
    for sl_session in  sl_sessions:
        print(sl_session)
        session = sl_session.name
        subject = sl_session.parent.name

        qqc_output = qqc_root / subject / session
        quick_figures(sl_session, qqc_output)


def test_SL_figures():
    rawdata_root = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata')
    qqc_root = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/')
    sl_sessions = rawdata_root.glob('sub-SL*/ses-*')
    for sl_session in  sl_sessions:
        print(sl_session)
        session = sl_session.name
        subject = sl_session.parent.name

        qqc_output = qqc_root / subject / session
        quick_figures(sl_session, qqc_output)

def test_SL_create_html():
    qqc_root = Path('/data/predict1/data_from_nda/MRI_ROOT/derivatives/quick_qc/')
    gif_paths = list(qqc_root.glob('sub-SL*/ses-*/*176*PA*dwi.gif'))
    # Function to extract date from filename
    import re
    def extract_date(filename):
        match = re.search(r'ses-(\d{8})', str(filename))
        return match.group(1) if match else '00000000'  # Default if no date found

    # Sort the list by the extracted date
    gif_paths.sort(key=extract_date)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Gallery of GIFs</title>
    </head>
    <body>
    <h1>My GIF Gallery</h1>
    {image_tags}
    </body>
    </html>
    """

    # Generate image tags for each GIF
    image_tags = ''.join(f'<img src="{path}" alt="Image" style="width:300px;"><br>' for path in gif_paths)

    # Insert the image tags into the HTML template
    html_content = html_template.format(image_tags=image_tags)

    # Write the HTML content to a file
    with open('gallery.html', 'w') as file:
        file.write(html_content)

