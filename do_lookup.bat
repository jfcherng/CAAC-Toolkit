@ECHO OFF

REM The department ID of NTHU EE "Jia" Group
SET department_NthuEe_Jia=011322
REM The department ID of NTHU EE "Yi" Group
SET department_NthuEe_Yi=011332

python lookup.py --outputFormat="NthuEe" --output="NTHU-EE-A.csv" --departmentIds=%department_NthuEe_Jia%
python lookup.py --outputFormat="NthuEe" --output="NTHU-EE-B.csv" --departmentIds=%department_NthuEe_Yi%
python lookup.py --outputFormat="NthuEe" --output="NTHU-EE-AB.csv" --departmentIds=%department_NthuEe_Jia%,%department_NthuEe_Yi%

PAUSE