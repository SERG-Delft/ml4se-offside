import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.LinkedHashMap;
import java.util.List;

/**
 * Simple class that parses all files within the directory specified by dirPath (can also be provided as a parameter if
 * called from the command line). Simply writes all pairs of original methods and mutated methods to corresponding files.
 * Everything is done synchronously as this is only meant for testing and debugging purposes. Run on large datasets at
 * your own risk.
 */
public class GenerateMutations {
    private static String dirPath;
    private static Path originalMethodPath;
    private static Path mutatedMethodPath;

    public static void main(String[] args) {
        dirPath = "C:\\Users\\Lenovo\\Downloads\\java-med\\test\\airbnb__lottie-android";
        if (args.length > 0) dirPath = args[0];
        originalMethodPath = Paths.get(System.getProperty("user.dir"),  "originalMethods.txt");
        mutatedMethodPath = Paths.get(System.getProperty("user.dir"),  "x-men.txt");
        try {
            FileWriter ofw = new FileWriter(originalMethodPath.toString());
            FileWriter mfw = new FileWriter(mutatedMethodPath.toString());
            ofw.close();
            mfw.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        parseAllFilesFound();
    }

    private static void parseAllFilesFound() {
        try {
            Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java"))
                    .forEach(path -> {
                        ExtractionTask task = new ExtractionTask(path);
                        LinkedHashMap<String, List<MethodDeclaration>> map = task.processFile();

                        writeMethodsToFile(map);

                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void writeMethodsToFile(LinkedHashMap<String, List<MethodDeclaration>> map) {
        try {
            FileWriter originalMethodsWriter = new FileWriter(originalMethodPath.toString(),true);
            originalMethodsWriter.write(map.get("0").toString());
            originalMethodsWriter.close();

            FileWriter mutatedMethodsWriter = new FileWriter(mutatedMethodPath.toString(),true);
            mutatedMethodsWriter.write(map.get("1").toString());
            mutatedMethodsWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
