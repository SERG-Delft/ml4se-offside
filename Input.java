int helloWorldBug(int n) {
    int[] array = new int[n];
    for (int i = 0; i <= n; i++) {
        array[i] = i;
    }
    return array;
}

int helloWorldNoBug(int n) {
    int[] array = new int[n];
    for (int i = 0; i < n; i++) {
        array[i] = i;
    }
    return array;
}