import pandas as pd
from pathlib import Path
from ampscz_asana.models.subject import Subject


def add_subjects(db_session, phoenix_roots: list):
    for phoenix_root in phoenix_roots:
        phoenix_root = Path(phoenix_root)
        network = phoenix_root.parent.name
        metadata_pattern_str = f'GENERAL/{network}*/{network}*_metadata.csv'
        metadata_locs = list(phoenix_root.glob(metadata_pattern_str))
        for metadata_loc in metadata_locs:
            subject_ids = pd.read_csv(metadata_loc)['Subject ID'].tolist()
            for subject_id in subject_ids:
                if subject_id != 'CA00152':
                    pass
                    # continue
                network_site = network + subject_id[:2]
                network_dir = phoenix_root / 'PROTECTED' / network_site
                mri_dir = network_dir / 'raw' / subject_id / 'mri'
                subject_obj = Subject(subject_id=subject_id,
                                      site=subject_id[:2],
                                      network=network,
                                      phoenix_mri_dir=str(mri_dir))

                # Check if subject exists
                existing_subject = db_session.query(Subject).filter_by(
                        subject_id=subject_id).first()

                # Add subject if it doesn't exist
                if existing_subject is None:
                    db_session.add(subject_obj)
                    db_session.commit()
                    print("Subject added:", subject_obj)
                else:
                    print("Subject already exists:", existing_subject)
            # return


def update_subjects(db_session, phoenix_roots):
    all_subjects = []
    for phoenix_root in phoenix_roots:
        phoenix_root = Path(phoenix_root)
        network = phoenix_root.parent.name
        metadata_pattern_str = f'GENERAL/{network}*/{network}*_metadata.csv'
        metadata_locs = list(phoenix_root.glob(metadata_pattern_str))
        for metadata_loc in metadata_locs:
            all_subjects += pd.read_csv(metadata_loc)['Subject ID'].tolist()

    subjects = db_session.query(Subject).all()
    for subject in subjects:
        if subject.subject_id not in all_subjects:
            db_session.delete(subject)
    db_session.commit()


