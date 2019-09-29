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

            for (MethodDeclaration method : methods) {
                System.out.println(method.getName());
                try {
                    extractContextPath("0", method.toString());
                } catch (IOException | InterruptedException e) {
                    e.printStackTrace();
                }
            }
            System.out.println();
            System.out.println("Mutated Methods");
            for (MethodDeclaration mutatedMethod : mutatedMethods) {
                System.out.println(mutatedMethod.getName());
            }
            for (MethodDeclaration mutatedMethod : mutatedMethods) {
                try {
                    extractContextPath("1", mutatedMethod.toString());
                } catch (IOException | InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private static void extractContextPath(String type, String code) throws IOException, InterruptedException {
        code = code.replace(Character.toString('"'), "\\" + "\"");
        System.out.println(code);
        Path currentPath = Paths.get(System.getProperty("user.dir"), "src", "main", "java");
        Path contextExtractorPath = Paths.get(currentPath.toString(), "JavaExtractor-0.0.2-SNAPSHOT.jar");
        ProcessBuilder pb = new ProcessBuilder("java", "-cp", contextExtractorPath.toString(), "JavaExtractor.App", "--max_path_length", maxPathLength, "--max_path_width", maxPathWidth, "--code", code, "--no_hash");
        Process p = pb.start();

        BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));

        String message = in.lines().collect(Collectors.joining());

        ArrayList<String> result = new ArrayList<>();
        for (String line : message.split("\\r?\\n")) {
            ArrayList<String> parts = new ArrayList<>(Arrays.asList(line.trim().split(" ")));
            String methodName = parts.get(0);
            ArrayList<String> currentResultLineParts = new ArrayList<>(Collections.singletonList(type));
            parts.remove(0);
            Iterator<String> partsIterator = parts.iterator();
            int i = 0;
            while (partsIterator.hasNext() && i < maxContexts) {
                String[] contextParts = partsIterator.next().split(",");
                String contextWord1 = contextParts[0];
                String contextPath = contextParts[1];
                String contextWord2 = contextParts[2];
                currentResultLineParts.add(contextWord1 + "," + contextPath + "," + contextWord2);
                i++;
            }
            String spacePadding = new String(new char[(maxContexts - parts.size() - 1)]).replace("\0", " ");
            String resultLine = String.join(" ", currentResultLineParts) + spacePadding;
            result.add(resultLine);
        }
        try (FileWriter fw = new FileWriter(outPutDir, true);
             BufferedWriter bw = new BufferedWriter(fw);
             PrintWriter out = new PrintWriter(bw)) {
            for (String contextPath : result) {
                out.println(contextPath);
            }
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
}
