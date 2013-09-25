class Program {
    public static void main(String[] args) {
        int[] x = new int[] { 1, 2, 3, 4 };
        for (int i = 0; i < x.length; i++) {
            if (x[i] < 3)
                System.out.println(x[i] + " low");
            if (x[i] > 3)
                System.out.println(x[i] + " high");
        }
    }
}
