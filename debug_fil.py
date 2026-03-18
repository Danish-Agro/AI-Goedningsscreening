#!/usr/bin/env python3
"""Kør: python3 debug_fil.py <sti-til-fil.xlsx>"""
import sys
import pandas as pd
import openpyxl

if len(sys.argv) < 2:
    print("Brug: python3 debug_fil.py <fil.xlsx>")
    sys.exit(1)

path = sys.argv[1]

wb = openpyxl.load_workbook(path)
print(f"Sheets: {wb.sheetnames}")

df = pd.read_excel(path, header=None)
print(f"Størrelse: {df.shape[0]} rækker × {df.shape[1]} kolonner")
print()
print("Rækker 0-13, kolonner 0-7:")
print(df.iloc[0:14, 0:8].to_string())
print()

# Find første ikke-tomme celle i rækkerne 4-8 (ordrenummer-området)
print("Scanning for ordrenummer (rækker 4-8, kolonner 0-10):")
for row in range(4, 9):
    for col in range(0, 11):
        try:
            val = df.iloc[row, col]
            if not pd.isna(val):
                print(f"  Række {row}, kolonne {col}: {repr(val)}")
        except IndexError:
            pass
