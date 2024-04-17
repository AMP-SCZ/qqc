from pathlib import Path
from configparser import ConfigParser
from typing import Dict


def config(path: Path, section: str) -> Dict[str, str]:
    """
    Read the configuration file and return a dictionary of parameters for the given section.

    Args:
        filename (str): The path to the configuration file.
        section (str): The section of the configuration file to read.

    Returns:
        dict: A dictionary of parameters for the given section.

    Raises:
        Exception: If the specified section is not found in the configuration file.
    """
    parser = ConfigParser()
    parser.read(path)

    conf = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            conf[param[0]] = param[1]
    else:
        raise ValueError(f"Section {section} not found in the {path} file")

    return conf


def test_query(db_session):
    from sqlalchemy.orm import join, joinedload

    # query = db_session.query(Qqc).options(joinedload(SessionNum.session_num))
    # query = db_session.query(
            # Qqc.qqc_executed, Qqc.qqc_completed,
            # SessionNum.session_num, SessionDate.session_date).join(
            # SessionNum).join(SessionDate)
    # query = db_session.query(
            # Qqc.qqc_executed, Qqc.qqc_completed,
            # SessionNum.session_num, SessionDate.session_date).join(
            # SessionNum).join(SessionDate).all()
    query = db_session.query(
            Subject.subject_id,
            MriZip.filename,
            SessionDate.session_date,
            SessionNum.session_num,
            MriRunSheet.matching_date_and_ses_num,
            Qqc.qqc_executed, Qqc.qqc_completed).select_from(Subject).join(
            MriZip).join(SessionDate).join(SessionNum).join(MriRunSheet).join(Qqc)

    query = db_session.query(
            Subject.subject_id,
            MriZip.filename,
            SessionDate.session_date,
            SessionNum.session_num,
            SessionNum.has_run_sheet,
            MriRunSheet.matching_date_in_zip,
            MriRunSheet.matching_date_and_ses_num,
            Qqc.qqc_executed, Qqc.qqc_completed
            ).select_from(Subject).outerjoin(
            MriZip).outerjoin(SessionDate).outerjoin(SessionNum).outerjoin(MriRunSheet).outerjoin(Qqc)

    query = db_session.query(
            Subject.subject_id,
            MriZip.filename,
            SessionDate.session_date,
            SessionNum.session_num,
            SessionNum.has_run_sheet,
            MriRunSheet.matching_date_in_zip,
            MriRunSheet.matching_date_and_ses_num,
            MriRunSheet.run_sheet_scan_date,
            ).select_from(Subject).join(
            MriZip, full=True).join(SessionDate, full=True).join(
                    SessionNum, full=True).join(MriRunSheet, full=True)
    print(query.statement)
    with open('query_command.txt', 'w') as fp:
        fp.write(query.statement.__str__())
        # fp.write(query.statement)
    # Convert query result to pandas DataFrame
    df = pd.read_sql(query.statement, query.session.bind)
    print(df)
    df.to_csv('test.csv')


def check_if_running(process_name: str) -> bool:
    """
    Check if a process with the same path is running in the background.

    Args:
        process_name (str): The name of the process to check.

    Returns:
        bool: True if the process is running, False otherwise.
    """
    command = f"ps -ef | grep -v grep | grep -c {process_name}"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, check=False)
    num_processes = int(result.stdout.decode("utf-8"))
    return num_processes > 0
