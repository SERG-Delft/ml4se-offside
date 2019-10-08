import com.github.javaparser.ParseProblemException;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.stmt.IfStmt;

import java.util.List;
import java.util.Random;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class MethodExtractor {
    private final Random rand = new Random();

    public MethodExtractor() {}

    public List<MethodDeclaration> extractMethodsFromCode(String code) {
        CompilationUnit parsedClass = null;
        try {
            parsedClass = StaticJavaParser.parse(code);
        } catch (ParseProblemException e) {
            //System.out.println("Failed to parse string: " + code);
        }
        return extractMethodsFromClass(parsedClass);
    }

    private List<MethodDeclaration> extractMethodsFromClass(CompilationUnit parsedClass) {
        return parsedClass.findAll(MethodDeclaration.class).stream()
                .filter(this::containsBinaryWithOffByOne)
                .collect(Collectors.toList());
    }

    public MethodDeclaration mutateMethod(MethodDeclaration method) {
        MethodDeclaration mutatedMethod = method.clone();

        List<BinaryExpr> mutationCandidates = mutatedMethod.findAll(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .collect(Collectors.toList());

        int mutationIndex = rand.nextInt(mutationCandidates.size());
        mutateExpression(mutationCandidates.get(mutationIndex));


        return mutatedMethod;
    }

    private void mutateExpression(BinaryExpr expression) {
        BinaryExpr.Operator operator = expression.getOperator();
        if (operator.equals(BinaryExpr.Operator.GREATER)) expression.setOperator(BinaryExpr.Operator.GREATER_EQUALS);
        else if (operator.equals(BinaryExpr.Operator.GREATER_EQUALS)) expression.setOperator(BinaryExpr.Operator.GREATER);
        else if (operator.equals(BinaryExpr.Operator.LESS_EQUALS)) expression.setOperator(BinaryExpr.Operator.LESS);
        else if (operator.equals(BinaryExpr.Operator.LESS)) expression.setOperator(BinaryExpr.Operator.LESS_EQUALS);
    }

    private boolean containsIfStmt(MethodDeclaration method) {
        return method.findAll(IfStmt.class).size() != 0;
    }

    private boolean containsBinaryWithOffByOne(MethodDeclaration method) {
        return method.findAll(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .toArray().length != 0;
    }

    private Predicate<BinaryExpr> containsOffByOne() {
        return expr -> expr.getOperator().equals(BinaryExpr.Operator.GREATER) ||
                expr.getOperator().equals(BinaryExpr.Operator.GREATER_EQUALS) ||
                expr.getOperator().equals(BinaryExpr.Operator.LESS) ||
                expr.getOperator().equals(BinaryExpr.Operator.LESS_EQUALS);
    }
}