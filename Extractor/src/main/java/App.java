import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class App {
    private static String dirPath;
    private static String maxPathLength;
    private static String maxPathWidth;
    private static int maxContexts;
    private static String outPutDir;

    private static Instant start;

    private static int threadCount;

    private static long totalCount = 0;

    private static ReentrantLock failCountLock = new ReentrantLock();
    private static int failCount = 0;

    private static int[] count = {0};

    private static ReentrantLock doneLock = new ReentrantLock();
    private static int doneCount = 0;

    private static ReentrantLock writerLock = new ReentrantLock();
    private static PrintWriter outWriter;

    private static void finalStats() {
        long secondsElapsed = Duration.between(start, Instant.now()).getSeconds();
        System.out.println("Task finished");
        System.out.println("Total amount of files: " + totalCount);
        System.out.println("Files failed to be parsed: " + failCount);
        System.out.println("Time elapsed: " +
                String.format("%d:%02d:%02d",
                        secondsElapsed / 3600, (secondsElapsed % 3600) / 60, secondsElapsed % 60));
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        dirPath = args[0];
        outPutDir = args[1];
        maxPathLength = args[2];
        maxPathWidth = args[3];
        maxContexts = Integer.parseInt(args[4]);
        threadCount = Integer.parseInt(args[5]);
        start = Instant.now();
        System.out.println("Starting parsing with " + threadCount + " threads");

        outWriter = new PrintWriter(new BufferedWriter(new FileWriter(outPutDir, true)));

        extractDir();
    }

    private static void extractDir() throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        try {
            totalCount = Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java")).count();

            Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java")).
                    forEach(path -> {
                        Runnable extractor = new ExtractionThread(new ExtractionTask(path), count[0]);
                        executor.execute(extractor);
                        ++count[0];
                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
        executor.shutdown();
        while (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
            doneLock.lock();
            System.out.println("Awaiting completion. Completed: " + doneCount + " of " + totalCount);
            doneLock.unlock();
        }
        finalStats();
    }

    public static class ExtractionThread implements Runnable{
        private ExtractionTask extractor;
        private String fileNameTemplate;

        public ExtractionThread(ExtractionTask extractor, int threadId) {
            this.extractor = extractor;
            this.fileNameTemplate = "correct" + threadId + ".txt";
        }

        @Override
        public void run() {
            try {
                printMethodsAndContextPathsToFile(extractor.processFile());
            } catch (Exception e) {
                System.out.println("Failed to process file " + extractor.filePath);
                failCountLock.lock();
                doneLock.lock();
                ++doneCount;
                ++failCount;
                doneLock.unlock();
                failCountLock.unlock();
            }
        }

        private void printMethodsAndContextPathsToFile(LinkedHashMap<String, List<MethodDeclaration>> methodsAndMutatedMethods) throws IOException {
            List<MethodDeclaration> methods = methodsAndMutatedMethods.get("0");
            List<MethodDeclaration> mutatedMethods = methodsAndMutatedMethods.get("1");

            PrintWriter writer = new PrintWriter(new FileWriter(fileNameTemplate, false));

            for (MethodDeclaration method : methods) {
                writer.println(method);
                writer.println();
            }
            writer.close();
            extractContextPathFromFile("0", fileNameTemplate);

            writer = new PrintWriter(new FileWriter("in" + fileNameTemplate, false));

            for (MethodDeclaration mutatedMethod : mutatedMethods) {
                writer.println(mutatedMethod);
                writer.println();
            }
            writer.close();
            extractContextPathFromFile("0", "in" + fileNameTemplate);
            doneLock.lock();
            ++doneCount;
            doneLock.unlock();
        }

        private void extractContextPathFromFile(String type, String fileName) throws IOException {
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
            writerLock.lock();
            for (String contextPath : result) {
                outWriter.println(contextPath);
            }
            writerLock.unlock();
            new File(fileName).delete();
        }
    }
}