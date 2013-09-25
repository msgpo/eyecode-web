class Program {
    static void add_1(int num) {
        num = num + 1;
    }

    static void twice(int num) {
        num = num * 2;
    }

    public static void main(String[] args) {
        int added = 4;
        add_1(added);
        twice(added);
        add_1(added);
        twice(added);
        System.out.println(added);
    }
}
