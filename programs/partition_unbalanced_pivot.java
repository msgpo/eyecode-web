class Program {
    public static void main(String[] args) {
        int pivot = 3;
        int[] x = new int[] { 1, 2, 3, 4 };
        for (int i = 0; i < x.length; i++) {
            if (x[i] < pivot)
                System.out.println(x[i] + " low");
            if (x[i] > pivot)
                System.out.println(x[i] + " high");
        }
    }
}
