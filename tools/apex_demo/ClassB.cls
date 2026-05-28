public class ClassB {
    public static String methodB() {
        String fromC = ClassC.methodC();
        return 'ClassB received -> ' + fromC;
    }
}
