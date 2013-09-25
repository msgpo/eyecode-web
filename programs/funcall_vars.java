class Program {
    static int f(int x) {
        return x + 4;
    }

    public static void main(String[] args) {
        int x = f(1);
        int y = f(0);
        int z = f(-1);
        System.out.println(x * y * z);
    }
}
