class Program {
    public static void main(String[] args) {
        int intercept = 1;
        int slope = 5;

        int x_base = 0;
        int x_other = x_base + 1;
        int x_end = x_base + x_other + 1;

        int y_base = slope * x_base + intercept;
        int y_other = slope * x_other + intercept;
        int y_end = slope * x_end + intercept;

        System.out.println(x_base + " " + y_base);
        System.out.println(x_other + " " + y_other);
        System.out.println(x_end + " " + y_end);
    }
}
