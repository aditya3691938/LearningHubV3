import pandas as pd
import io

def parse_assessment_csv(file_stream, filename=None):
    """
    Parses assessment CSV or Excel file with columns:
    Serial Number, Question, Option 1 (or Option1), Option 2 (or Option 2), Option 3 (or Option 3), Option 4 (or Option 4), Option 5 (or Option 5) (Optional), Correct Option
    Returns tuple: (questions_list, errors_list)
    """
    questions = []
    errors = []

    try:
        # Determine whether to read CSV or Excel
        if filename and (str(filename).lower().endswith('.xlsx') or str(filename).lower().endswith('.xls')):
            df = pd.read_excel(file_stream)
        else:
            try:
                df = pd.read_csv(file_stream)
            except Exception:
                if hasattr(file_stream, 'seek'):
                    file_stream.seek(0)
                df = pd.read_excel(file_stream)
        
        # Clean column names (strip whitespace)
        df.columns = [str(c).strip() for c in df.columns]

        # Standardize column headers (map "Option 1" to "Option1", "Option 2" to "Option2", etc.)
        col_mapping = {}
        for col in df.columns:
            cleaned = col.replace(' ', '').replace('_', '').lower()
            if cleaned in ['option1', 'opt1']:
                col_mapping[col] = 'Option1'
            elif cleaned in ['option2', 'opt2']:
                col_mapping[col] = 'Option2'
            elif cleaned in ['option3', 'opt3']:
                col_mapping[col] = 'Option3'
            elif cleaned in ['option4', 'opt4']:
                col_mapping[col] = 'Option4'
            elif cleaned in ['option5', 'opt5']:
                col_mapping[col] = 'Option5'
            elif cleaned in ['serialnumber', 'slno', 'sno', 'sn', 'srno']:
                col_mapping[col] = 'Serial Number'
            elif cleaned in ['correctoption', 'answer', 'correctanswer', 'correct']:
                col_mapping[col] = 'Correct Option'
            elif cleaned in ['question', 'q']:
                col_mapping[col] = 'Question'

        if col_mapping:
            df = df.rename(columns=col_mapping)

        required_cols = ['Question', 'Option1', 'Option2', 'Option3', 'Option4', 'Correct Option']
        
        # Check if required columns exist or map by position if 7 columns
        if len(df.columns) >= 7 and not all(c in df.columns for c in required_cols):
            # Positional mapping (without Option 5)
            df.columns = ['Serial Number', 'Question', 'Option1', 'Option2', 'Option3', 'Option4', 'Correct Option'] + list(df.columns[7:])

        for idx, row in df.iterrows():
            row_num = idx + 1
            question_text = str(row.get('Question', '')).strip()
            opt1 = str(row.get('Option1', '')).strip()
            opt2 = str(row.get('Option2', '')).strip()
            opt3 = str(row.get('Option3', '')).strip()
            opt4 = str(row.get('Option4', '')).strip()
            opt5 = str(row.get('Option5', '')).strip()
            if opt5.lower() == 'nan':
                opt5 = ''
            correct = str(row.get('Correct Option', '')).strip()

            if not question_text or question_text.lower() == 'nan':
                errors.append(f"Row {row_num}: Question is empty.")
                continue

            if not opt1 or not opt2 or not opt3 or not opt4 or any(x.lower() == 'nan' for x in [opt1, opt2, opt3, opt4]):
                errors.append(f"Row {row_num}: All 4 options are required.")
                continue

            if not correct or correct.lower() == 'nan':
                errors.append(f"Row {row_num}: Correct Option is empty.")
                continue

            # Normalize correct option (e.g., 'Option 1' -> 'Option1', '1' -> 'Option1', etc.)
            correct_clean = correct.replace(' ', '').replace('_', '')
            if correct_clean.lower() in ['1', 'option1', 'opt1', 'a']:
                correct = 'Option1'
            elif correct_clean.lower() in ['2', 'option2', 'opt2', 'b']:
                correct = 'Option2'
            elif correct_clean.lower() in ['3', 'option3', 'opt3', 'c']:
                correct = 'Option3'
            elif correct_clean.lower() in ['4', 'option4', 'opt4', 'd']:
                correct = 'Option4'
            elif correct_clean.lower() in ['5', 'option5', 'opt5', 'e']:
                correct = 'Option5'

            serial_num = int(row.get('Serial Number', row_num)) if str(row.get('Serial Number', '')).isdigit() else row_num

            questions.append({
                'serial_number': serial_num,
                'question': question_text,
                'option1': opt1,
                'option2': opt2,
                'option3': opt3,
                'option4': opt4,
                'option5': opt5 if opt5 else None,
                'correct_option': correct
            })

    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")

    return questions, errors


def resolve_option_index(val, q):
    if not val:
        return None
    val_str = str(val).strip()
    if not val_str:
        return None
    val_clean = val_str.lower().replace(' ', '').replace('_', '').replace('-', '')
    if val_clean in ['option1', 'opt1', '1', 'a']:
        return 1
    if val_clean in ['option2', 'opt2', '2', 'b']:
        return 2
    if val_clean in ['option3', 'opt3', '3', 'c']:
        return 3
    if val_clean in ['option4', 'opt4', '4', 'd']:
        return 4
    if val_clean in ['option5', 'opt5', '5', 'e']:
        return 5

    for idx in range(1, 6):
        opt_text = str(getattr(q, f'option{idx}', '') or '').strip()
        if not opt_text:
            continue
        opt_clean = opt_text.lower().replace(' ', '').replace('_', '').replace('-', '')
        if val_clean == opt_clean or val_str.lower() == opt_text.lower():
            return idx

    return None


def evaluate_assessment(questions, user_answers, pass_percentage=80.0):
    """
    Evaluates user answers dictionary {question_id: selected_option}.
    Returns (score_percentage, passed, total_questions, correct_count)
    """
    if not questions:
        return 100.0, True, 0, 0

    correct_count = 0
    total = len(questions)

    for q in questions:
        user_val = user_answers.get(str(q.id)) or user_answers.get(q.id) or user_answers.get(f"q_{q.id}")
        user_idx = resolve_option_index(user_val, q)
        correct_idx = resolve_option_index(getattr(q, 'correct_option', ''), q)

        if user_idx is not None and correct_idx is not None and user_idx == correct_idx:
            correct_count += 1

    score_percentage = round((correct_count / total) * 100.0, 2)
    passed = score_percentage >= float(pass_percentage)

    return score_percentage, passed, total, correct_count
