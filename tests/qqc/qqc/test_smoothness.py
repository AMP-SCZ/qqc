from qqc.qqc.smoothness import summary_smoothness_table_for_a_session


def test_summary_smoothness_table_for_a_session():
    subject = 'SF29950'
    session = '202401041'
    summary_smoothness_table_for_a_session(subject, session)
