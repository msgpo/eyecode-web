import java.util.ArrayList;

class Program {
    static ArrayList between(int[] numbers, int low, int high) {
        ArrayList winners = new ArrayList();
        for (int i = 0; i < numbers.length; i++)
            if ((low < numbers[i]) && (numbers[i] < high))
                winners.add(numbers[i]);
        return winners;
    }

    static ArrayList common(int[] list1, int[] list2) {
        ArrayList winners = new ArrayList();
        for (int i = 0; i < list1.length; i++)
            for (int j = 0; j < list2.length; j++)
                if (list1[i] == list2[j])
                    winners.add(list1[i]);
        return winners;
    }

    public static void main(String[] args) {
        int[] x = new int[] { 2, 8, 7, 9, -5, 0, 2 };
        ArrayList xBtwn = between(x, 2, 10);
        System.out.println(xBtwn.toString());

        int[] y = new int[] { 1, -3, 10, 0, 8, 9, 1 };
        ArrayList yBtwn = between(y, -2, 9);
        System.out.println(yBtwn.toString());

        ArrayList xyCommon = common(x, y);
        System.out.println(xyCommon.toString());
    }
}
