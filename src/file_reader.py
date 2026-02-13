import pandas as pd
import io

class DataFileReader:
    
    @staticmethod
    def detect_separator(file_content: str, max_lines: int = 5):
        lines = file_content.split('\n')[:max_lines]
        
        separators = [',', ';', '\t', '|', ' ']
        separator_counts = {}
        
        for sep in separators:
            counts = [line.count(sep) for line in lines if line.strip()]
            if counts and all(c == counts[0] and c > 0 for c in counts):
                separator_counts[sep] = counts[0]
        
        if separator_counts:
            return max(separator_counts, key=separator_counts.get)
        
        return ','
    
    @staticmethod
    def read_file(uploaded_file, sheet_name=None):
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        try:
            if file_extension == 'csv':
                content = uploaded_file.getvalue().decode('utf-8')
                separator = DataFileReader.detect_separator(content)
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=separator)
                return df, f"CSV (separator: '{separator}')"
            
            elif file_extension in ['xlsx', 'xls']:
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                
                if sheet_name is None:
                    sheet_name = sheet_names[0]
                
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                return df, f"Excel (sheet: '{sheet_name}')", sheet_names
            
            elif file_extension == 'json':
                df = pd.read_json(uploaded_file)
                return df, "JSON"
            
            elif file_extension == 'txt':
                content = uploaded_file.getvalue().decode('utf-8')
                separator = DataFileReader.detect_separator(content)
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=separator)
                return df, f"TXT (separator: '{separator}')"
            
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        
        except UnicodeDecodeError: # Ujjwal?
            uploaded_file.seek(0)
            content = uploaded_file.getvalue().decode('latin-1')
            separator = DataFileReader.detect_separator(content)
            df = pd.read_csv(io.StringIO(content), sep=separator)
            return df, f"{file_extension.upper()} (separator: '{separator}', encoding: latin-1)"
        
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    @staticmethod
    def get_supported_formats():
        return ['csv', 'xlsx', 'xls', 'json', 'txt']
