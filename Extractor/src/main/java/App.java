import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class App {
    private static String dirPath;
    private static List<MethodDeclaration> methods = new ArrayList<>();
    private static List<MethodDeclaration> mutatedMethods = new ArrayList<>();

    public static void main(String[] args) {
        dirPath = args[0];
//        dirPath = "C:/Users/Lenovo/OneDrive/Skóli/Master/Machine Learning for Software Analysis/Project/repo/training/ACRA__acra/acra/src/main/java/org/acra";
        extractDir();
    }

    private static void extractDir() {
        ExecutorService executor = Executors.newCachedThreadPool();
        LinkedList<ExtractionTask> tasks = new LinkedList<>();
        try {
            Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java"))
                    .forEach(path -> {
                        ExtractionTask task = new ExtractionTask(path);
                        tasks.add(task);
                    });
        } catch (IOException e) {
            e.printStackTrace();
            return;
        }
        try {
            executor.invokeAll(tasks);
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            executor.shutdown();

            System.out.println("Original Methods");
            System.out.println(methods);
            System.out.println();
            System.out.println("Mutated Methods");
            System.out.println(mutatedMethods);
        }
    }

    public static void addToMethods(List<MethodDeclaration> newMethods) {
        methods.addAll(newMethods);
    }

    public static void addToMutatedMethods(List<MethodDeclaration> newMutatedMethods) {
        mutatedMethods.addAll(newMutatedMethods);
    }
}
