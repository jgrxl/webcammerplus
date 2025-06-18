/**
 * Simple test to verify Jest is working
 */

describe('Basic Jest Test', () => {
    test('should pass basic assertion', () => {
        expect(1 + 1).toBe(2);
    });
    
    test('should handle arrays', () => {
        const arr = [1, 2, 3];
        expect(arr).toHaveLength(3);
        expect(arr).toContain(2);
    });
    
    test('should handle objects', () => {
        const obj = { name: 'test', value: 123 };
        expect(obj).toHaveProperty('name');
        expect(obj.value).toBe(123);
    });
    
    test('should handle async operations', async () => {
        const promise = Promise.resolve('success');
        await expect(promise).resolves.toBe('success');
    });
});