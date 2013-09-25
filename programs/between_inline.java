import java.util.ArrayList;

class Program {
    public static void main(String[] args) {
        int[] x = new int[] { 2, 8, 7, 9, -5, 0, 2 };
        ArrayList xBtwn = new ArrayList();
        for (int i = 0; i < x.length; i++)
            if ((2 < x[i]) && (x[i] < 10))
                xBtwn.add(x[i]);

        System.out.println(xBtwn.toString());

        int[] y = new int[] { 1, -3, 10, 0, 8, 9, 1 };
        ArrayList yBtwn = new ArrayList();
        for (int i = 0; i < y.length; i++)
            if ((-2 < y[i]) && (y[i] < 9))
                yBtwn.add(y[i]);

        System.out.println(yBtwn.toString());

        ArrayList xyCommon = new ArrayList();
        for (int i = 0; i < x.length; i++)
            for (int j = 0; j < y.length; j++)
                if (x[i] == y[j])
                    xyCommon.add(x[i]);

        System.out.println(xyCommon.toString());
    }
}
