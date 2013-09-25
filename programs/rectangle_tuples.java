class Program {
    static int area(int[] xy_1, int[] xy_2) {
        int width = xy_2[0] - xy_1[0];
        int height = xy_2[1] - xy_1[1];
        return width * height;
    }

    public static void main(String[] args) {
        int[] r1_xy_1 = new int[] { 0, 0 };
        int[] r1_xy_2 = new int[] { 10, 10 };
        int r1_area = area(r1_xy_1, r1_xy_2);
        System.out.println(r1_area);

        int[] r2_xy_1 = new int[] { 5, 5 };
        int[] r2_xy_2 = new int[] { 10, 10 };
        int r2_area = area(r2_xy_1, r2_xy_2);
        System.out.println(r2_area);
    }
}
