from pathlib import Path
import subprocess


# Looking into file for if/while statements and append negation for entire condition
def openFileForIfAndWhile(path):
    subs = [' if ', ' while ']
    subprocess.call(['java', '-jar', 'google-java-format-1.7-all-deps.jar', '--replace', path])
    with open(path) as file:
        lines = file.readlines()
        mutCount = 1
        for l in lines:
            for sub in subs:
                if (sub in l) and ('!' not in l) and ('&&' not in l) and ('||' not in l):
                    savedLine = l
                    index = lines.index(l)
                    lines[index] = insertExMarkInIfAndWhile(l, sub)
                    with open(path + '.mut' + "{}".format(mutCount), "w+") as mutation:
                        mutation.writelines(lines)
                    mutCount += 1
                    lines[index] = savedLine
                if (sub + ' (!' in l) and ('&&' not in l) and ('||' not in l):
                    savedLine = l
                    index = lines.index(l)
                    lines[index] = removeExMarkInIfAndWhile(l, sub)
                    with open(path + '.mut' + "{}".format(mutCount), "w+") as mutation:
                        mutation.writelines(lines)
                    mutCount += 1
                    lines[index] = savedLine


# Inserting negation for entire condition
def insertExMarkInIfAndWhile(line, sub):
    index = line.find(sub)
    line = line[:index + len(sub)] + '(!' + line[index + len(sub):len(line) - 3] + ')' + line[len(line) - 3:]
    return line


# Removing negation from condition
def removeExMarkInIfAndWhile(line, sub):
    index = line.find(sub)
    line = line[:index + len(sub)] + line[index + len(sub) + 2:len(line) - 4] + line[len(line) - 3:]
    return line


# Get all .java files and create mutations for if/while statements
def main():
    javaFiles = list(Path(".").rglob("*.java"))
    for file in javaFiles:
        openFileForIfAndWhile(file.absolute().as_posix())


if __name__ == "__main__":
    main()
