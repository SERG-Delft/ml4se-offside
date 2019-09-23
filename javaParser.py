import glob
from pathlib import Path
import subprocess


# Looking into file for if statement and append negation for entire condition
def openFileForIf(path):
    print('Formatting file ' + path)
    subprocess.call(['java', '-jar', 'google-java-format-1.7-all-deps.jar', '--replace', path])
    with open(path) as file:
        lines = file.readlines()
        print('File read')
        mutCount = 1
        for l in lines:
            if ' if ' in l:
                print('if statement found in string ' + l)
                savedLine = l
                index = lines.index(l)
                lines[index] = insertExMarkInIf(l)
                print('Writing mutation')
                with open(path + '.mut' + "{}".format(mutCount), "w+") as mutation:
                    mutation.writelines(lines)
                mutCount += 1
                lines[index] = savedLine
        with open(path + '.orig', "w+") as orig:
            orig.writelines(lines)


# Inserting negation for entire condition
def insertExMarkInIf(line):
    index = line.find(' if ')
    print('Original: ' + line)
    line = line[:index + 4] + '(!' + line[index + 4:len(line) - 3] + ')' + line[len(line) - 3:]
    print('Modified: ' + line)
    return line


# Get all .java files and create mutations for if statements
def main():
    javaFiles = list(Path(".").rglob("*.java"))
    for file in javaFiles:
        openFileForIf(file.absolute().as_posix())


if __name__ == "__main__":
    main()
