import pexpect
sh = pexpect.spawn("/usr/local/cellar/open-adventure/1.20/bin/advent", encoding="utf-8", timeout=5)
sh.expect(r"\>")          # initial prompt
print(sh.before)
sh.sendline("n")
sh.expect(r"\>")
print(sh.before)          # output of last command
