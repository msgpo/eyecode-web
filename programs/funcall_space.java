class Program {
    static int f(int x) {
        return x + 4;
    }

    public static void main(String[] args) {
        System.out.println( f(1) * f(0) * f(-1) );
    }
}
