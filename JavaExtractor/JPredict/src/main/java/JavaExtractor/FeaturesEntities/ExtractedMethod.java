package JavaExtractor.FeaturesEntities;

import com.github.javaparser.ast.body.MethodDeclaration;

public class ExtractedMethod {
    private MethodDeclaration method;
    private String originalOperator;
    private String containingNode;

    public ExtractedMethod(MethodDeclaration method, String originalOperator, String containingNode) {
        this.method = method;
        this.originalOperator = originalOperator;
        this.containingNode = containingNode;
    }

    public MethodDeclaration getMethod() {
        return method;
    }

    public void setMethod(MethodDeclaration method) {
        this.method = method;
    }

    public String getOriginalOperator() {
        return originalOperator;
    }

    public void setOriginalOperator(String originalOperator) {
        this.originalOperator = originalOperator;
    }

    public String getContainingNode() {
        return containingNode;
    }

    public void setContainingNode(String containingNode) {
        this.containingNode = containingNode;
    }
}
