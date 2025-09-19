import subprocess, sys, time
proc = subprocess.Popen([sys.executable, "-u", "-c",
    "import sys,time; [sys.stdout.write(f'L{i}\\n') or sys.stdout.flush() or time.sleep(0.2) for i in range(3)]"],
    stdout=subprocess.PIPE, text=True, bufsize=1)

for line in proc.stdout:
    print("GOT:", line, end="")
print("EXIT", proc.wait())
