package JavaExtractor.Common;

import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;

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
}
