package JavaExtractor.Common;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseProblemException;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;

import java.util.List;
import java.util.Random;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class MethodExtractor {
    private final Random rand = new Random();

    public MethodExtractor() {}

    public List<MethodDeclaration> extractMethodsFromCode(String code) {
        final String classPrefix = "public class Test {";
        final String classSuffix = "}";
        final String methodPrefix = "SomeUnknownReturnType f() {";
        final String methodSuffix = "return noSuchReturnValue; }";

        String originalContent = code;
        String content = originalContent;
        CompilationUnit parsedClass = null;
        try {
            parsedClass = JavaParser.parse(content);
        } catch (ParseProblemException e1) {
            // Wrap with a class and method
            try {
                content = classPrefix + methodPrefix + originalContent + methodSuffix + classSuffix;
                parsedClass = JavaParser.parse(content);
            } catch (ParseProblemException e2) {
                // Wrap with a class only
                content = classPrefix + originalContent + classSuffix;
                parsedClass = JavaParser.parse(content);
            }
        }
        return extractMethodsFromClass(parsedClass);
    }

    private List<MethodDeclaration> extractMethodsFromClass(CompilationUnit parsedClass) {
        return parsedClass.getNodesByType(MethodDeclaration.class).stream()
                .filter(this::containsBinaryWithOffByOne)
                .collect(Collectors.toList());
    }

    public MethodDeclaration mutateMethod(MethodDeclaration method) {
        MethodDeclaration mutatedMethod = (MethodDeclaration) method.clone();

        List<BinaryExpr> mutationCandidates = mutatedMethod.getNodesByType(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .collect(Collectors.toList());

        int mutationIndex = rand.nextInt(mutationCandidates.size());
        mutateExpression(mutationCandidates.get(mutationIndex));


        return mutatedMethod;
    }

    private void mutateExpression(BinaryExpr expression) {
        BinaryExpr.Operator operator = expression.getOperator();
        if (operator.equals(BinaryExpr.Operator.greater)) expression.setOperator(BinaryExpr.Operator.greaterEquals);
        else if (operator.equals(BinaryExpr.Operator.greaterEquals)) expression.setOperator(BinaryExpr.Operator.greater);
        else if (operator.equals(BinaryExpr.Operator.lessEquals)) expression.setOperator(BinaryExpr.Operator.less);
        else if (operator.equals(BinaryExpr.Operator.less)) expression.setOperator(BinaryExpr.Operator.lessEquals);
    }

    private boolean containsBinaryWithOffByOne(MethodDeclaration method) {
        return method.getNodesByType(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .toArray().length != 0;
    }

    private Predicate<BinaryExpr> containsOffByOne() {
        return expr -> expr.getOperator().equals(BinaryExpr.Operator.greater) ||
                expr.getOperator().equals(BinaryExpr.Operator.greaterEquals) ||
                expr.getOperator().equals(BinaryExpr.Operator.less) ||
                expr.getOperator().equals(BinaryExpr.Operator.lessEquals);
    }
}