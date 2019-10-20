package JavaExtractor.Common.Statistics;

public class OperatorType {

    public enum Type {
        greater, greaterEquals, less, lessEquals
    }

    private Type type;
    private long count = 0;

    public OperatorType(Type type) {
        this.type = type;
    }

    public Type getType() {
        return type;
    }

    public synchronized void increment(long inc) {
        this.count += inc;
    }

    public long getCount() {
        return count;
    }
}
