import subprocess

def main():
    args = "/usr/local/cellar/open-adventure/1.20/bin/advent"

    # subprocess.run(args)

    # p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # for line in p.stdout:
    #     print(line)
    print(p.stdout.readline())
    # p.stdin.write("n\nquit\ny\n")


    print("hello")

if __name__ == "__main__":
    main()
