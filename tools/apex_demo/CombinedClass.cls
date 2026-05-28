public class CombinedClass {
    public static String methodA() {
        String fromB = methodB();
        return 'ClassA received -> ' + fromB;
    }

    public static String methodB() {
        String fromC = methodC();
        return 'ClassB received -> ' + fromC;
    }

    public static String methodC() {
        String fromD = methodD();
        return 'ClassC received -> ' + fromD;
    }

    public static String methodD() {
        return 'Return from ClassD.methodD';
    }
}
