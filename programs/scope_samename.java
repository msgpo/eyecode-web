class Program {
    static void add_1(int added) {
        added = added + 1;
    }

    static void twice(int added) {
        added = added * 2;
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
