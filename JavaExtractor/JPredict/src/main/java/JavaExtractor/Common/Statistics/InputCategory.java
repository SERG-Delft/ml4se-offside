package JavaExtractor.Common.Statistics;

public class InputCategory {
    private String name;
    private long count = 0;

    public InputCategory(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }


    public long getCount() {
        return count;
    }

    public synchronized void increment(long inc) {
        this.count += inc;
    }
}
