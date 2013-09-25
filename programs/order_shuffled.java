class Program {
    static int h(int x) {
        return f(x) + g(x);
    }

    static int f(int x) {
        return x + 4;
    }

    static int g(int x) {
        return x * 2;
    }

    public static void main(String[] args) {
        int x = 1;
        int a = f(x);
        int b = g(x);
        int c = h(x);
        System.out.println(a + " " + b + " " + c);
    }
}
