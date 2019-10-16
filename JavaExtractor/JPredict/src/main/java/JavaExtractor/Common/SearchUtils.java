package JavaExtractor.Common;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.EnclosedExpr;
import com.github.javaparser.ast.expr.UnaryExpr;

import java.util.function.Predicate;

public class SearchUtils {



    public static boolean containsBinaryWithOffByOne(MethodDeclaration method) {
        return method.getNodesByType(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .toArray().length != 0;
    }

    public static Predicate<BinaryExpr> containsOffByOne() {
        return expr -> expr.getOperator().equals(BinaryExpr.Operator.greater) ||
                expr.getOperator().equals(BinaryExpr.Operator.greaterEquals) ||
                expr.getOperator().equals(BinaryExpr.Operator.less) ||
                expr.getOperator().equals(BinaryExpr.Operator.lessEquals);
    }

    public static Class<? extends Node> getContainingNodeType(BinaryExpr binaryExpr) {
        Node parent = binaryExpr.getParentNode();
        while (parent instanceof BinaryExpr || parent instanceof EnclosedExpr || parent instanceof UnaryExpr) {
            parent = parent.getParentNode();
        }
        return parent.getClass();
    }

    public static Predicate<BinaryExpr> isContainedBy(Class<? extends Node> clazz) {
        return expr -> getContainingNodeType(expr).equals(clazz);
    }
}
