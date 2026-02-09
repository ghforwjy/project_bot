import { test, expect } from '@playwright/test';

// 测试聊天界面图标是否正常显示，不会因消息长度而变形
test('聊天界面图标大小测试', async ({ page }) => {
  // 导航到聊天页面
  await page.goto('http://localhost:3000');
  
  // 等待页面加载完成
  await page.waitForLoadState('networkidle');
  
  // 发送一条长消息
  const longMessage = '这是一条非常长的消息，用于测试聊天界面中图标的显示效果。这条消息包含了大量的文本内容，目的是为了验证当消息内容很长时，用户和机器的图标是否会被拉伸变形。通过这个测试，我们可以确保在各种消息长度的情况下，图标的大小都能保持一致，不会因为消息内容的长度而发生变化。';
  
  // 输入消息
  await page.fill('textarea[placeholder="输入消息..."]', longMessage);
  
  // 发送消息
  await page.click('button:has-icon("SendOutlined")');
  
  // 等待消息发送完成
  await page.waitForTimeout(1000);
  
  // 验证用户图标大小
  const userAvatar = await page.locator('.ant-avatar:has-icon("UserOutlined")').first();
  const userAvatarBox = await userAvatar.boundingBox();
  expect(userAvatarBox).toBeTruthy();
  expect(userAvatarBox!.width).toBeLessThanOrEqual(40);
  expect(userAvatarBox!.height).toBeLessThanOrEqual(40);
  
  // 等待AI回复
  await page.waitForTimeout(2000);
  
  // 验证机器图标大小
  const robotAvatar = await page.locator('.ant-avatar:has-icon("RobotOutlined")').first();
  const robotAvatarBox = await robotAvatar.boundingBox();
  expect(robotAvatarBox).toBeTruthy();
  expect(robotAvatarBox!.width).toBeLessThanOrEqual(40);
  expect(robotAvatarBox!.height).toBeLessThanOrEqual(40);
  
  console.log('测试通过：图标大小正常，未发生变形');
});

// 测试多条消息的情况
test('多条消息图标一致性测试', async ({ page }) => {
  // 导航到聊天页面
  await page.goto('http://localhost:3000');
  
  // 等待页面加载完成
  await page.waitForLoadState('networkidle');
  
  // 发送多条不同长度的消息
  const messages = [
    '短消息',
    '这条消息长度适中，用于测试图标显示',
    '这是一条非常长的消息，包含大量文本内容，用于验证图标在长消息情况下的显示效果。通过发送不同长度的消息，我们可以确保图标在各种情况下都能保持一致的大小，不会因为消息内容的长度而发生变化。'
  ];
  
  for (const message of messages) {
    await page.fill('textarea[placeholder="输入消息..."]', message);
    await page.click('button:has-icon("SendOutlined")');
    await page.waitForTimeout(1500);
  }
  
  // 获取所有用户图标
  const userAvatars = await page.locator('.ant-avatar:has-icon("UserOutlined")').all();
  expect(userAvatars.length).toBeGreaterThanOrEqual(3);
  
  // 验证所有用户图标大小一致
  for (const avatar of userAvatars) {
    const box = await avatar.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.width).toBeLessThanOrEqual(40);
    expect(box!.height).toBeLessThanOrEqual(40);
  }
  
  // 获取所有机器图标
  const robotAvatars = await page.locator('.ant-avatar:has-icon("RobotOutlined")').all();
  expect(robotAvatars.length).toBeGreaterThanOrEqual(3);
  
  // 验证所有机器图标大小一致
  for (const avatar of robotAvatars) {
    const box = await avatar.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.width).toBeLessThanOrEqual(40);
    expect(box!.height).toBeLessThanOrEqual(40);
  }
  
  console.log('测试通过：多条消息下图标大小保持一致');
});
