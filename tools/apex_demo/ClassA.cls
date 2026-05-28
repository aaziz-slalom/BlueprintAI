public class ClassA {
    public static String methodA() {
        String fromB = ClassB.methodB();
        return 'ClassA received -> ' + fromB;
    }
}
