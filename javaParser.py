from pathlib import Path
import subprocess
import random


# Looking into file for if/while statements and append negation for entire condition
# SUBJECT FOR DELETION
def openFileForIfAndWhile2(path):
    subs = [' if ', ' while ']
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
                if (sub + '(!' in l) and ('&&' not in l) and ('||' not in l):
                    savedLine = l
                    index = lines.index(l)
                    lines[index] = removeExMarkInIfAndWhile(l, sub)
                    with open(path + '.mut' + "{}".format(mutCount), "w+") as mutation:
                        mutation.writelines(lines)
                    mutCount += 1
                    lines[index] = savedLine


# Looking into function lines for if/while statements and append negation for entire condition
def openFileForIfAndWhile(lines):
    subs = [' if ', ' while ']
    candidateLines = []
    funcList = [insertExMarkInIfAndWhile, removeExMarkInIfAndWhile]
    for l in lines:
        for sub in subs:
            if (sub in l) and ('!' not in l) and ('&&' not in l) and ('||' not in l):
                candidateLines.append([lines.index(l), 0, sub])
            if (sub + '(!' in l) and ('&&' not in l) and ('||' not in l):
                candidateLines.append([lines.index(l), 1, sub])
    if len(candidateLines) == 0:
        return
    strOrig = "".join(lines)
    candidate = random.choice(candidateLines)
    subLinePosition = candidate[0]
    func = candidate[1]
    sub = candidate[2]
    lines[subLinePosition] = funcList[func](lines[subLinePosition], sub)
    strMut = "".join(lines)
    return strOrig, [0.01, 0.01, 0.01], strMut, [0.99, 0.01, 0.01]


# Inserting negation for entire condition
def insertExMarkInIfAndWhile(line, sub):
    index = line.find(sub)
    line = line[:index + len(sub)] + '(!' + line[index + len(sub):len(line) - 3] + ')' + line[len(line) - 3:]
    return line


# Removing negation from entire condition
def removeExMarkInIfAndWhile(line, sub):
    index = line.find(sub)
    line = line[:index + len(sub)] + line[index + len(sub) + 2:len(line) - 4] + line[len(line) - 3:]
    return line


# Get all .java files and create mutations for if/while statements
def main():
    javaFiles = list(Path(".").rglob("*.java"))
    for file in javaFiles:
        path = file.absolute().as_posix()
        subprocess.call(['java', '-jar', 'google-java-format-1.7-all-deps.jar', '--replace', path])
        openFileForIfAndWhile2(path)


if __name__ == "__main__":
    main()
