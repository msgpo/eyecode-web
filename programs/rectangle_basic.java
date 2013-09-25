class Program {
    static int area(int x1, int y1, int x2, int y2) {
        int width = x2 - x1;
        int height = y2 - y1;
        return width * height;
    }

    public static void main(String[] args) {
        int r1_x1 = 0;
        int r1_y1 = 0;
        int r1_x2 = 10;
        int r1_y2 = 10;
        int r1_area = area(r1_x1, r1_y1, r1_x2, r1_y2);
        System.out.println(r1_area);

        int r2_x1 = 5;
        int r2_y1 = 5;
        int r2_x2 = 10;
        int r2_y2 = 10;
        int r2_area = area(r2_x1, r2_y1, r2_x2, r2_y2);
        System.out.println(r2_area);
    }
}
