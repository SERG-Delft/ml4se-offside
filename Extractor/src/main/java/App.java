import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

public class App {
    private static String dirPath;
    private static String maxPathLength;
    private static String maxPathWidth;
    private static int maxContexts;
    private static String outPutDir;
    private static List<MethodDeclaration> methods = new ArrayList<>();
    private static List<MethodDeclaration> mutatedMethods = new ArrayList<>();

    public static void main(String[] args) {
        dirPath = Paths.get(System.getProperty("user.dir")).toString();
        outPutDir = "myfile.txt";
        maxPathLength = "8";
        maxPathWidth = "2";
        maxContexts = 200;
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

            printMethods();
            System.out.println("Original Methods");

            try {
                extractContextPath("0", "originals.txt");
                extractContextPath("1", "mutants.txt");
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private static void extractContextPath(String type, String fileName) throws IOException, InterruptedException {
        Path currentPath = Paths.get(System.getProperty("user.dir"), "src", "main", "java");
        Path contextExtractorPath = Paths.get(currentPath.toString(), "JavaExtractor-0.0.2-SNAPSHOT.jar");
        ProcessBuilder pb = new ProcessBuilder("java", "-cp", contextExtractorPath.toString(), "JavaExtractor.App", "--max_path_length", maxPathLength, "--max_path_width", maxPathWidth, "--file", fileName, "--no_hash");
        Process p = pb.start();

        BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));

        String message = in.lines().collect(Collectors.joining());
        try (FileWriter fw = new FileWriter(outPutDir, true);
             BufferedWriter bw = new BufferedWriter(fw);
             PrintWriter out = new PrintWriter(bw)) {
            out.println(type);
            out.println(message);
        } catch (IOException e) {
            System.out.println("exception occoured: " + e);
        }
    }

    public static void addToMethods(List<MethodDeclaration> newMethods) {
        methods.addAll(newMethods);
    }

    public static void addToMutatedMethods(List<MethodDeclaration> newMutatedMethods) {
        mutatedMethods.addAll(newMutatedMethods);
    }

    public static void printMethods() {
        try {
            PrintWriter writer = new PrintWriter("originals.txt", "UTF-8");

            for (MethodDeclaration method : methods) {
                writer.println(method);
                writer.println();
            }
            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            PrintWriter writer = new PrintWriter("mutants.txt", "UTF-8");

            for (MethodDeclaration mutatedMethod : mutatedMethods) {
                writer.println(mutatedMethod);
                writer.println();
            }
            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
