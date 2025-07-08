import pandas as pd

try:
    # Try different encodings
    encodings = ['utf-8', 'latin1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            print(f"Trying encoding: {encoding}")
            df = pd.read_csv('data/amazon.csv', nrows=5, encoding=encoding)
            print(f"Success with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            print(f"Failed with encoding: {encoding}")
            continue
        except Exception as e:
            print(f"Other error with encoding {encoding}: {str(e)}")
            continue
    
    if df is not None:
        print("\nColumns:")
        print(df.columns.tolist())
        print("\nFirst few rows:")
        print(df.head())
        print("\nData types:")
        print(df.dtypes)
    else:
        print("Could not read the file with any of the attempted encodings")
        
except Exception as e:
    print(f"Error: {str(e)}")
