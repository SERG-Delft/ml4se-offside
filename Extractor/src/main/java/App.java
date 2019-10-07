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

    private static Instant start;

    private static int threadCount;

    private static long totalCount = 0;

    private static ReentrantLock failCountLock = new ReentrantLock();
    private static int failCount = 0;

    private static int[] count = {0};

    private static ReentrantLock doneLock = new ReentrantLock();
    private static int doneCount = 0;

    private static PrintWriter finalWriter;

    private static void finalStats() {
        long secondsElapsed = Duration.between(start, Instant.now()).getSeconds();
        System.out.println("Task finished");
        System.out.println("Total amount of files: " + totalCount);
        System.out.println("Files failed to be parsed: " + failCount);
        System.out.println("Time elapsed: " + String.format("%d:%02d:%02d",
                        secondsElapsed / 3600, (secondsElapsed % 3600) / 60, secondsElapsed % 60));
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        dirPath = args[0]; //absolute path to training data root
        String outPutDir = args[1]; //"resultfile.txt";
        maxPathLength = args[2]; //"8"
        maxPathWidth = args[3]; //"2"
        maxContexts = Integer.parseInt(args[4]); //200;
        threadCount = Integer.parseInt(args[5]); // around 10 (depends on the computer)
        start = Instant.now();
        System.out.println("Starting parsing with " + threadCount + " threads");

        finalWriter = new PrintWriter(new FileWriter(outPutDir, false));

        extractDir();
    }

    private static void extractDir() throws InterruptedException, IOException {
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        ArrayList<ExtractionThread> threads = new ArrayList<>();
        try {
            totalCount = Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java")).count();

            Files.walk(Paths.get(dirPath)).filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".java")).
                    forEach(path -> {
                        ExtractionThread extractor = new ExtractionThread(new ExtractionTask(path), count[0]);
                        threads.add(extractor);
                        executor.execute(extractor);
                        ++count[0];
                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
        executor.shutdown();
        while (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
            doneLock.lock();
            failCountLock.lock();
            System.out.println("Awaiting completion. Completed: " + doneCount + " of " + totalCount + ". Failed to parse: " + failCount);
            failCountLock.unlock();
            doneLock.unlock();
        }
        Instant parseEnd = Instant.now();
        long secondsElapsed = Duration.between(start, parseEnd).getSeconds();
        System.out.println("Parsing completed in " + String.format("%d:%02d:%02d",
                secondsElapsed / 3600, (secondsElapsed % 3600) / 60, secondsElapsed % 60));

        for (ExtractionThread extractor : threads) {
            for (String line : extractor.getThreadResult()) {
                finalWriter.println(line);
            }
        }
        finalWriter.close();
        secondsElapsed = Duration.between(parseEnd, Instant.now()).getSeconds();
        System.out.println("Merging completed in " + String.format("%d:%02d:%02d",
                secondsElapsed / 3600, (secondsElapsed % 3600) / 60, secondsElapsed % 60));
        finalStats();
    }

    public static class ExtractionThread implements Runnable{
        private ExtractionTask extractor;
        private String tempFileNameTemplate;
        private String resultFileName;
        private PrintWriter outWriter;

        public ExtractionThread(ExtractionTask extractor, int threadId) {
            this.extractor = extractor;
            this.tempFileNameTemplate = "correct" + threadId + ".txt";
            this.resultFileName = "tempResult" + threadId + ".txt";
        }

        public ArrayList<String> getThreadResult() throws IOException{
            ArrayList<String> result = new ArrayList<>();
            BufferedReader br = null;
            try {
                br = new BufferedReader(new FileReader(resultFileName));
            }
            catch (Exception ex) {
                return result;
            }
            String line = br.readLine();
            while (line != null) {
                result.add(line);
                line = br.readLine();
            }
            new File(resultFileName).delete();
            return result;
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
            outWriter = new PrintWriter(new FileWriter(resultFileName, false));

            List<MethodDeclaration> methods = methodsAndMutatedMethods.get("0");
            List<MethodDeclaration> mutatedMethods = methodsAndMutatedMethods.get("1");

            PrintWriter writer = new PrintWriter(new FileWriter(tempFileNameTemplate, false));

            for (MethodDeclaration method : methods) {
                writer.println(method);
                writer.println();
            }
            writer.close();
            extractContextPathFromFile("0", tempFileNameTemplate);

            writer = new PrintWriter(new FileWriter("in" + tempFileNameTemplate, false));

            for (MethodDeclaration mutatedMethod : mutatedMethods) {
                writer.println(mutatedMethod);
                writer.println();
            }
            writer.close();
            extractContextPathFromFile("1", "in" + tempFileNameTemplate);
            doneLock.lock();
            ++doneCount;
            doneLock.unlock();
            outWriter.close();
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
            for (String line : lines) {
                ArrayList<String> parts = new ArrayList<>(Arrays.asList(line.trim().split(" ")));
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
                String resultString = String.join(" ", currentResultLineParts);
                for (i = 0; i < maxContexts - parts.size(); ++i) {
                    resultString = resultString + " ";
                }
                outWriter.println(resultString);
            }
            new File(fileName).delete();
        }
    }
}

