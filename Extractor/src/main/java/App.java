import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class App {
    private static String dirPath;
    private static String maxPathLength;
    private static String maxPathWidth;
    private static int maxContexts;
    private static String outPutDir;

    public static void main(String[] args) {
        dirPath = args[0];//Paths.get(System.getProperty("user.dir")).toString();
        outPutDir = args[1];//"myfile.txt";
        maxPathLength = args[2];//"8";
        maxPathWidth = args[3];//"2";
        maxContexts = Integer.parseInt(args[4]);//200;
        extractDir();
    }

    private static void extractDir() {
        ExecutorService executor = Executors.newCachedThreadPool();
        LinkedList<ExtractionTask> tasks = new LinkedList<>();
        try {
            Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java"))
                    .forEach(path -> {
                        ExtractionTask extractor = new ExtractionTask(path);
                        printMethodsAndContextPathsToFile(extractor.processFile());
                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void extractContextPathFromFile(String type, String fileName) throws IOException {
        Path currentPath = Paths.get(System.getProperty("user.dir"), "src", "main", "java");
        Path contextExtractorPath = Paths.get(currentPath.toString(), "JavaExtractor-0.0.2-SNAPSHOT.jar");
        ProcessBuilder pb = new ProcessBuilder("java", "-cp", contextExtractorPath.toString(), "JavaExtractor.App", "--max_path_length", maxPathLength, "--max_path_width", maxPathWidth, "--file", fileName, "--no_hash");
        Process p = pb.start();

        BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String contextPathForMethod;
        ArrayList<String> lines = new ArrayList<>();
        while ((contextPathForMethod = in.readLine()) != null) {
            lines.add(contextPathForMethod);
        }
        ArrayList<String> result = new ArrayList<>();
        for (String line : lines) {
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
            String resultLine = String.join(" ", currentResultLineParts);
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

    public static void printMethodsAndContextPathsToFile(LinkedHashMap<String, List<MethodDeclaration>> methodsAndMutatedMethods) {
        List<MethodDeclaration> methods = methodsAndMutatedMethods.get("0");
        List<MethodDeclaration> mutatedMethods = methodsAndMutatedMethods.get("1");
        try {
            PrintWriter writer = new PrintWriter(new FileWriter("correct.txt", false));

            for (MethodDeclaration method : methods) {
                writer.println(method);
                writer.println();
            }
            writer.close();
            extractContextPathFromFile("0", "correct.txt");
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            PrintWriter writer = new PrintWriter(new FileWriter("incorrect.txt", false));

            for (MethodDeclaration mutatedMethod : mutatedMethods) {
                writer.println(mutatedMethod);
                writer.println();
            }
            writer.close();
            extractContextPathFromFile("0", "incorrect.txt");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
