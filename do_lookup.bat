@ECHO OFF

REM �M�ؤj�� �q���t �Ҳ� �� �t�ҽs��
SET department_A=011322
REM �M�ؤj�� �q���t �A�� �� �t�ҽs��
SET department_B=011332

python lookup.py --departmentIds=%department_A% --output="NTHU-EE-A.csv"
python lookup.py --departmentIds=%department_B% --output="NTHU-EE-B.csv"
python lookup.py --departmentIds=%department_A%,%department_B% --output="NTHU-EE-AB.csv"

PAUSE
