package JavaExtractor.Common.Statistics;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.ConditionalExpr;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.stmt.*;

public enum ContainingNode {
    FOR(ForStmt.class, "For loop"),
    WHILE(WhileStmt.class, "While loop"),
    TERNARY(ConditionalExpr.class, "Ternary"),
    IF(IfStmt.class, "If statement"),
    RETURN(ReturnStmt.class, "Return statement"),
    METHOD(MethodCallExpr.class, "Method call"),
    DO(DoStmt.class, "Do statement"),
    ASSIGN(AssignExpr.class, "Value assignment"),
    ASSERT(AssertStmt.class, "Assertion"),
    VARIABLEDECLARATOR(VariableDeclarator.class, "Boolean declaration"), //boolean isLeaving = position < EXIT_THRESHOLD;
    OBJECTCREATION(ObjectCreationExpr.class, "Object creation"), //operation = new RemoveFamily(r < 12);
    EXPRESSION(ExpressionStmt.class, "Lambda expression"); //nodes.stream().filter( it -> it.getComments().size() > 0).count() >= 0;

    private Class<? extends Node> nodeClass;
    private String name;

    ContainingNode(Class<? extends Node> nodeClass, String name) {
        this.nodeClass = nodeClass;
        this.name = name;
    }

    public Class<? extends Node> getNodeClass() {
        return nodeClass;
    }

    public String getName() {
        return name;
    }
}
