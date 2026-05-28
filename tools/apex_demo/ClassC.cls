public class ClassC {
    public static String methodC() {
        String fromD = ClassD.methodD();
        return 'ClassC received -> ' + fromD;
    }
}
