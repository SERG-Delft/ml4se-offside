import com.github.javaparser.ast.body.MethodDeclaration;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;

public class ExtractionTask {
    Path filePath;
    private MethodExtractor methodExtractor;

    public ExtractionTask(Path path) {
        this.filePath = path;
        this.methodExtractor = new MethodExtractor();
    }

/*    @Override
    public Void call() throws Exception {
        processFile();
        return null;
    }*/

    public LinkedHashMap processFile() {
        String code = "";
        try {
            code = new String(Files.readAllBytes(this.filePath));
        } catch (IOException e) {
            //e.printStackTrace();
        }

        List<MethodDeclaration> methods = methodExtractor.extractMethodsFromCode(code);
        List<MethodDeclaration> mutatedMethods = new ArrayList<>();
        for (MethodDeclaration method : methods) {
            mutatedMethods.add(methodExtractor.mutateMethod(method));
        }

        LinkedHashMap methodsAndMutatedMethods = new LinkedHashMap<String, List<MethodDeclaration>>();
        methodsAndMutatedMethods.put("0", methods);
        methodsAndMutatedMethods.put("1", mutatedMethods);

        return methodsAndMutatedMethods;
    }
}
